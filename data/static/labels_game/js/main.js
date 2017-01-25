var results = [];
var seenCount = 0;
var correctCount = 0;
var wrongCount = 0;
var items = [];
var answer = false;
var currentLabel = null;
var currentCaption = null;
var currentDescription = null;
var currentFoodId = null;

function shuffle(array) {
	var currentIndex = array.length, temporaryValue, randomIndex;

	// While there remain elements to shuffle...
	while (0 !== currentIndex) {

		// Pick a remaining element...
		randomIndex = Math.floor(Math.random() * currentIndex);
		currentIndex -= 1;

		// And swap it with the current element.
		temporaryValue = array[currentIndex];
		array[currentIndex] = array[randomIndex];
		array[randomIndex] = temporaryValue;
	}

	return array;
}

var indices = [0,1,2,3,4];
var shuffledIndices = shuffle(indices);

var appendFood = function (item, tagged) {
	var index = shuffledIndices.pop();
	items[index] = {
		'foodDisplayName': item.displayName,
		'foodId': item.foodId,
		'foodImageUrl': item.images[0],
		'tagged': tagged
	};
};


var populateForm = function(items) {
	var descriptionElement = document.getElementById("description");
	descriptionElement.textContent = currentDescription;
	var captionElement = document.getElementById("caption");
	captionElement.textContent = currentCaption;
	for (var i = 0, len = items.length; i < len; i++) {
		var paneElement = document.getElementById("pane" + (i+1) + "FoodName");
		paneElement.textContent = items[i].foodDisplayName;
		$('#tinderslide').find('.pane' + (i+1) + ' .img').css('background', 'url(' + items[i].foodImageUrl + ') no-repeat scroll center center');
	}
};


var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
		var result = JSON.parse(this.responseText);
		console.log(result);
		currentLabel = result.label;
		currentCaption = result.caption;
		currentDescription = result.description;
		for (var i = 0, len = result.taggedFoods.length; i < len; i++) {
			var taggedFood = result.taggedFoods[i];
			appendFood(taggedFood, true);
		}
		var untaggedFood = result.untaggedFoods[0];
		currentFoodId = untaggedFood.foodId;
		appendFood(untaggedFood, false);

		populateForm(items);
	}
};

//xhttp.open('GET', 'http://localhost:5001/plash/fooditems/abcdefgh/_label', true);
xhttp.open('GET', 'http://dev-plash-server.us-west-2.elasticbeanstalk.com/plash/fooditems/abcdefgh/_label', true);
xhttp.setRequestHeader('x-api-key', 'random_hackathon_key_plash');
xhttp.send();

var handleSwipe = function(index, bool) {
	if (bool) {
		results.push(index);
	}
	seenCount++;
	if (seenCount >= 5) {
		finished();
	}
};

var finished = function() {
	console.log(items);
	console.log(results);

	for (var i = 0, len = results.length; i < len; i++) {
		var itemMarkedYes = items[results[i]];
		if (itemMarkedYes.tagged) {
			correctCount++;
		} else {
			answer = true;
		}
	}

	wrongCount = 4 - correctCount;

	var requestData = {
		correct_count: correctCount,
		wrong_count: wrongCount,
		food_id: currentFoodId,
		label: currentLabel,
		answer: answer
	};
	console.log(requestData);
	var xhttp2 = new XMLHttpRequest();
	xhttp2.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
		}
	};
	//xhttp2.open('POST', 'http://localhost:5001/plash/users/abcdefgh', true);
	xhttp2.open('POST', 'http://dev-plash-server.us-west-2.elasticbeanstalk.com/plash/users/abcdefgh', true);
	xhttp2.setRequestHeader('x-api-key', 'random_hackathon_key_plash');
	xhttp2.setRequestHeader("Content-Type", "application/json");
	xhttp2.send(JSON.stringify(requestData));

	showScore();
};


var showScore = function() {
	var scoreElement = document.getElementById("score");
	scoreElement.textContent = "Congrats! you scored " + (correctCount+1) + "/" + 5;
};


$("#tinderslide").jTinder({
	// dislike callback
    onDislike: function (item) {
	    // set the status text
        $('#status').html('Dislike image ' + (item.index()+1));
		handleSwipe(item.index(), false);
    },
	// like callback
    onLike: function (item) {
	    // set the status text
        $('#status').html('Like image ' + (item.index()+1));
		handleSwipe(item.index(), true);
    },
	animationRevertSpeed: 200,
	animationSpeed: 400,
	threshold: 1,
	likeSelector: '.like',
	dislikeSelector: '.dislike'
});

/**
 * Set button action to trigger jTinder like & dislike.
 */
$('.actions .like, .actions .dislike').click(function(e){
	e.preventDefault();
	$("#tinderslide").jTinder($(this).attr('class'));
});
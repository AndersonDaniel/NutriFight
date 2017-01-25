// Create our 'main' state that will contain the game

var WIDTH = 1300;
var HEIGHT = 700;

var GROUND = 30 * HEIGHT / 31;
var FLOORWIDTH = 5;

HOR_SPEED = 300;

var nutrients = [
    ['potassium', 'banana.png', 100, 0, 0xFFFF99, 666306],
    ['vitamin_c', 'orange.png', 140, 0, 0xFFB137, 666401],
    ['vitamin_a', 'carrot.png', 180, 0, 0x33CC33, 666318],
    ['fibers', 'oats.png', 220, 0, 0xFFCC99, 291],
    ['calcium', 'bone.png', 260, 0, 0xFFFFFF, 666301],
    ['iron', 'spin.png', 300, 0, 0x009900]
]

function applyNutrients(food_nutrients) {
    for (var i = 0; i < nutrients.length; i++) {
        if (food_nutrients[nutrients[i][5]]) {
            nutrients[i][3] += food_nutrients[nutrients[i][5]].amount;
        }
    }
}

var mainState = {
    preload: function() {
        game.load.image('nutrinoman', 'assets/nutrinoman.png');
        game.load.image('background', 'assets/background.png');
        game.load.image('monster', 'assets/sugar_monster.png');

        for (var i = 0; i < nutrients.length; i++) {
            game.load.image(nutrients[i][0], 'assets/' + nutrients[i][1]);
        }

        game.time.advancedTiming = true;
    },

    addMonster: function() {
        var monster = game.add.sprite(WIDTH, GROUND, 'monster');
        monster.y -= monster.height;
        game.physics.arcade.enable(monster);
        monster.body.velocity.x = -5 * HOR_SPEED;
        monster.bringToTop();
        monster.checkWorldBounds = true;
        monster.outOfBoundKill = true;
        this.monsters.add(monster);
    },

    getRandomFoodItem: function() {
        if (this.restarting) {
            return;
        }

        var self = this;
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                result = JSON.parse(this.responseText);
                var food = result.foods[0];
                self.loadFood(food.images[0], WIDTH, HEIGHT / 2 * (Math.random() * 0.75 + 1), food);
            } else if (this.readystate == 4) {
                console.log('error!');
                console.log(result);
            }
        }

        xhttp.open('GET', '/plash/fooditems/anderson/_random', true);
        xhttp.setRequestHeader('x-api-key', 'random_hackathon_key_plash');
        xhttp.send();
    },

    loadFood: function(url, x, y, details) {
        var self = this;
        var food = game.add.sprite(x, y);
        food.details = details;
        var bmp = game.make.bitmapData();
        game.load.onFileComplete.removeAll();
        game.load.onFileComplete.add(function() {
            bmp.load('food');
            bmp.processPixelRGB(function(pix) {
                if (pix.r == 255 && pix.g == 255 && pix.b == 255)
                pix.a = 0;
                return pix;
            }, this);

            food.loadTexture(bmp);
            food.x = x;
            self.nutrinoman.bringToTop();
            game.physics.arcade.enable(food);
            food.body.velocity.x = -HOR_SPEED;
            scale = 1 / (food.height / 50);
            food.scale.setTo(scale);
            food.checkWorldBounds = true;
            food.outOfBoundKill = true;
            self.foods.add(food);
        });

        game.load.image('food', '/plash/food/' + url);
        game.load.start();
    },

    create: function() {
        this.background = game.add.tileSprite(0, 0, WIDTH, HEIGHT, 'background');

        game.physics.startSystem(Phaser.Physics.ARCADE);

        this.graphics = game.add.graphics(0, 0);

        window.graphics = this.graphics;

        this.nutrinoman = game.add.sprite(100, 245, 'nutrinoman');

        game.physics.arcade.enable(this.nutrinoman);
        this.nutrinoman.bringToTop();

        this.nutrinoman.body.gravity.y = 1000;

        var spaceKey = game.input.keyboard.addKey(Phaser.Keyboard.SPACEBAR);
        spaceKey.onDown.add(this.jump, this);
        this.foods = game.add.group();
        this.monsters = game.add.group();

        this.timer = game.time.events.loop(5000, function() {
            if (Math.random() > 0.3) {
                this.getRandomFoodItem();
            }
            if (Math.random() > 0.4) {
                this.addMonster();
            }
        }, this);

        this.score = 0;
        this.labelScore = game.add.text(20, 20, "0", {font: "30px Tahoma", fill: "#ffffff"});

        this.floor = game.add.sprite(0, GROUND);
        game.physics.enable(this.floor, Phaser.ARCADE);
        this.floor.body.immovable = true;
        this.floor.body.width = this.game.world.width;

        for (var i = 0; i < nutrients.length; i++) {
            curr = game.add.sprite(20, nutrients[i][2], nutrients[i][0]);
        }
    },

    update: function() {
        this.restarting = false;
        if (this.nutrinoman.y < 0 || this.nutrinoman.y > HEIGHT) {
            this.restartGame();
        }

        game.physics.arcade.collide(this.floor, this.nutrinoman);

        game.physics.arcade.collide(this.nutrinoman, this.foods, function(nutrinoman, food) {
            applyNutrients(food.details.foodItemMeasurementUnit[0].nutrients);
            food.destroy();
            nutrinoman.body.velocity.x = 0;
        });


        self = this;
        game.physics.arcade.collide(this.nutrinoman, this.monsters, function(nutrinoman, monster) {
            self.restartGame();
        });

        this.background.tilePosition.x -= 5;

        graphics.clear();
        for (var i = 0; i < nutrients.length; i++) {
            this.graphics.beginFill(nutrients[i][4], 1);
            rect_w = nutrients[i][3] * 10;
            graphics.drawRect(60, nutrients[i][2], rect_w, 25);
            graphics.endFill();
        }
    },

    jump: function() {
        if (this.nutrinoman.body.velocity.y == 0) {
            this.nutrinoman.body.velocity.y = -500 - 10 * nutrients[3][3];
        }
    },

    restartGame: function() {
        function restart() {
            game.load.removeAll();
            game.paused = false;
            game.state.start('main');
            for (var i = 0; i < nutrients.length; i++) {
                nutrients[i][3] = 0;
            }
        }

        game.load.onFileComplete.removeAll();
        restart();
    }
};

// Initialize Phaser, and create a 400px by 490px game
var game = new Phaser.Game(WIDTH, HEIGHT);

// Add the 'mainState' and call it 'main'
game.state.add('main', mainState);

// Start the state to actually start the game
game.state.start('main');
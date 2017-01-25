// Create our 'main' state that will contain the game

var WIDTH = 1300;
var HEIGHT = 700;

var GROUND = 30 * HEIGHT / 31;
var FLOORWIDTH = 5;

HOR_SPEED = 300;

var nutrients = [
    ['potassium', 'banana.png', 100, 0, 0xBABABA],
    ['vitamin_c', 'orange.png', 140, 0, 0xFFB137],
    ['vitamin_a', 'carrot.png', 180, 0, 0x33CC33],
    ['fibers', 'oats.png', 220, 0, 0xFFFFFF],
    ['fibers', 'fibers.png', 260, 0, 0xFFCC66]
]

var mainState = {
    preload: function() {
        game.load.image('bird', 'assets/nutrinoman.png');
        game.load.image('pipe', 'assets/pipe.png');
        game.load.image('cloud', 'assets/cloud.jpg');
        game.load.image('banana', '/banana');
        game.load.image('background', 'assets/background.png');

        for (var i = 0; i < nutrients.length; i++) {
            game.load.image(nutrients[i][0], 'assets/' + nutrients[i][1]);
        }

        game.time.advancedTiming = true;
    },

    loadFood: function(url, x, y) {
        var self = this;
        var food = game.add.sprite(500, 500);
        var bmp = game.make.bitmapData();
        game.load.onFileComplete.add(function() {
            console.log("finished loading");
            bmp.load('food');
            bmp.processPixelRGB(function(pix) {
                if (pix.r == 255 && pix.g == 255 && pix.b == 255)
                pix.a = 0;
                return pix;
            }, this);

            food.loadTexture(bmp);
            self.bird.bringToTop();
            game.physics.arcade.enable(food);
            food.body.velocity.x = -HOR_SPEED;
            food.scale.setTo(0.02);
        });

        console.log("starting to load");
        game.load.image('food', url);
        game.load.start();
    },

    create: function() {
        this.background = game.add.tileSprite(0, 0, WIDTH, HEIGHT, 'background');

        game.physics.startSystem(Phaser.Physics.ARCADE);

        this.graphics = game.add.graphics(0, 0);

        window.graphics = this.graphics;

        this.bird = game.add.sprite(100, 245, 'bird');

        game.physics.arcade.enable(this.bird);
        this.bird.bringToTop();

        this.bird.body.gravity.y = 1000;

        var spaceKey = game.input.keyboard.addKey(Phaser.Keyboard.SPACEBAR);
        spaceKey.onDown.add(this.jump, this);
        this.pipes = game.add.group();

        // this.timer = game.time.events.loop(1500, this.addCloud, this);

        this.score = 0;
        this.labelScore = game.add.text(20, 20, "0", {font: "30px Tahoma", fill: "#ffffff"});

        this.floor = game.add.sprite(0, GROUND);
        game.physics.enable(this.floor, Phaser.ARCADE);
        this.floor.body.immovable = true;
        this.floor.body.width = this.game.world.width;

        /*this.bmp = game.make.bitmapData();
        this.bmp.load('banana');
        this.bmp.processPixelRGB(function(pix) {
            if (pix.r == 255 && pix.g == 255 && pix.b == 255)
            pix.a = 0;
            return pix;
        }, this);*/

        for (var i = 0; i < nutrients.length; i++) {
            curr = game.add.sprite(20, nutrients[i][2], nutrients[i][0]);
        }

        this.loadFood('/banana', WIDTH, HEIGHT / 2);
    },

    update: function() {
        if (this.bird.y < 0 || this.bird.y > HEIGHT) {
            this.restartGame();
        }

        game.physics.arcade.collide(this.floor, this.bird);

        this.background.tilePosition.x -= 5;

        for (var i = 0; i < nutrients.length; i++) {
            this.graphics.beginFill(nutrients[i][4], 1);
            graphics.drawRect(60, nutrients[i][2], nutrients[i][3] * 10 + 30, 25);
            graphics.endFill();
        }
    },

    jump: function() {
        if (this.bird.body.velocity.y == 0) {
            this.bird.body.velocity.y = -500;
        }
    },

    restartGame: function() {
        game.state.start('main');
    }
};

// Initialize Phaser, and create a 400px by 490px game
var game = new Phaser.Game(WIDTH, HEIGHT);

// Add the 'mainState' and call it 'main'
game.state.add('main', mainState);

// Start the state to actually start the game
game.state.start('main');
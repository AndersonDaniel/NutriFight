// Create our 'main' state that will contain the game

var WIDTH = 1300;
var HEIGHT = 700;

var GROUND = 2 * HEIGHT / 3;
var FLOORWIDTH = 5;

HOR_SPEED = 300;

var mainState = {
    preload: function() {
        game.load.image('bird', 'assets/nutrinoman.png');
        game.load.image('pipe', 'assets/pipe.png');
        game.load.image('cloud', 'assets/cloud.jpg');

        game.time.advancedTiming = true;
    },

    addCloud: function() {
        var cloud = game.add.sprite(WIDTH, Math.random() * GROUND - 80, 'cloud');
        game.physics.arcade.enable(cloud);
        this.bird.bringToTop();
        cloud.body.velocity.x = -HOR_SPEED;
        cloud.checkWorldBounds = true;
        cloud.outOfBoundsKill = true;
    },

    addOnePipe: function(x, y) {
        var pipe = game.add.sprite(x, y, 'pipe');

        this.pipes.add(pipe);

        game.physics.arcade.enable(pipe);

        pipe.body.velocity.x = -200;

        pipe.checkWorldBounds = true;

        pipe.outOfBoundsKill = true;
    },

    addRowOfPipes: function() {
        var hole = Math.floor(Math.random() * 5) + 1;

        for (var i = 0; i < HEIGHT / 60; i++) {
            if (i != hole && i != hole + 1 && i != hole + 2) {
                this.addOnePipe(WIDTH, i * 60 + 10);
            }
        }

        this.score += 1;
        this.labelScore.text = this.score;
    },

    create: function() {
        game.stage.backgroundColor = '#71c5cf';
        game.physics.startSystem(Phaser.Physics.ARCADE);

        var graphics = game.add.graphics(0, 0);

        graphics.beginFill(0xFF3300);
        graphics.lineStyle(FLOORWIDTH, 0xffd900, 1);

        graphics.moveTo(0, GROUND);
        graphics.lineTo(WIDTH, GROUND);

        graphics.endFill();

        window.graphics = graphics;

        this.bird = game.add.sprite(100, 245, 'bird');

        game.physics.arcade.enable(this.bird);
        this.bird.bringToTop();

        this.bird.body.gravity.y = 1000;

        var spaceKey = game.input.keyboard.addKey(Phaser.Keyboard.SPACEBAR);
        spaceKey.onDown.add(this.jump, this);
        this.pipes = game.add.group();

        this.timer = game.time.events.loop(1500, this.addCloud, this);

        this.score = 0;
        this.labelScore = game.add.text(20, 20, "0", {font: "30px Tahoma", fill: "#ffffff"});

        this.floor = game.add.sprite(0, GROUND);
        game.physics.enable(this.floor, Phaser.ARCADE);
        this.floor.body.immovable = true;
        this.floor.body.width = this.game.world.width;
    },

    update: function() {
        if (this.bird.y < 0 || this.bird.y > HEIGHT) {
            this.restartGame();
        }

       game.physics.arcade.collide(this.floor, this.bird);
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
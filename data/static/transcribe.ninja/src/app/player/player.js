angular.module( 'transcribe-ninja.player', [
  'ui.router'
])

.directive('tnPlayer', function () { 
  return {
    restrict: 'E',
    templateUrl: 'player/player.tpl.html',
    link: function (scope, element, attrs) {
        var player = element.children()[0];


        scope.wavesurfer = Object.create(WaveSurfer);
        scope.loading_percent = 0;
        
        scope.wavesurfer.init({
          container: player,
          waveColor: '#c1c1c1',
          cursorColor: '#337ab7',
          progressColor: '#337ab7',
          minPxPerSec: 40
          // scrollParent: true,
          // pixelRatio: 1
        });

        scope.wavesurfer.on('play', function () {
            $('.fa-play')
              .removeClass('fa-play')
              .addClass('fa-pause');

            // Ya.Metrica
            yaCounter27735045.reachGoal('player_play');
        });

        scope.wavesurfer.on('pause', function () {
          $('.fa-pause')
              .removeClass('fa-pause')
          .addClass('fa-play');

          // Ya.Metrica
          yaCounter27735045.reachGoal('player_pause');
        });

        scope.wavesurfer.on('finish', function () {
          $('.fa-pause')
              .removeClass('fa-pause')
          .addClass('fa-play');

          // Ya.Metrica
          yaCounter27735045.reachGoal('player_finish');
        });

        scope.wavesurfer.on('loading', function (percent) {
          console.log(percent);
            scope.loading_percent = percent;
            scope.$apply();
        });

        scope.$watch(attrs.audioFile, function(value) {
          console.log(value, 'watch');

          if(typeof value == "undefined") {
            return;
          }

          scope.wavesurfer.clearRegions();
          scope.wavesurfer.load(value);
        });


        scope.duration = scope.wavesurfer.getDuration();
        
        if(typeof scope.playerInit != "undefined") {
          scope.playerInit();
          return;
        }

        scope.$on('$destroy', function() {
          scope.wavesurfer.destroy();
        });

    }
  };
})

;


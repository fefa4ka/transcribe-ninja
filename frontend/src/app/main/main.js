angular.module( 'transcribe-ninja.main', [
  'transcribe-ninja.order',
  'ui.router'
])

.config(function config( $stateProvider ) {
  $stateProvider.state( 'main', {
    url: '/',
    views: {
      "main": {
        controller: 'MainCtrl',
        templateUrl: 'main/main.tpl.html'
      }
    },
    data:{ pageTitle: 'Transcribe.ninja – стенографирование разговоров' }
  });
})
.directive('mainLogo', function () {
  return {
    restrict: 'E',
    templateUrl: 'main/main.logo.tpl.html',
    link: function (scope, element, attrs) {
      console.log('make logo');
    }
  };
})
.controller( 'MainCtrl', function MainCtrl( $scope, $interval, $translate, $modal, $log, api ) {
  $translate.use("ru");

  $scope.slogan_wave = {
    amplitude: 10,
    position: 30,
    direction: 1
  }
          $sloganFirstPath = $("#sloganFirstPath"),
          $sloganSecondPath = $("#sloganSecondPath");

          
  };

  
      wave = $interval(function(){
    if(index > max) {
            direction = -1;
        }
        if(index < min) {
            direction = 1;
        } 
        
        index = index + 2 * direction;
        var index_2 = (index - 30),
            index_4 = 220 + index,
            index_5 = index;
        
        path.attr("d", "M0,44 C17,"+index+" 90,31 189,31 C189,30 200,0 200,0");
        pathFirst.attr("d", "M0,44 C14,"+(index_2*-1)+" 69,19 101,27 C132,34 197,58 "+index_4+","+index_5);
  });

  $scope.upload = function() {
    console.log('upload');
  };



})

;

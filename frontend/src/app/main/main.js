angular.module( 'transcribe-ninja.main', [
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
.controller( 'MainCtrl', function MainCtrl( $scope, $translate) {
  $translate.use("ru");
  
  $scope.logoNameState = function($event) {
    var states = [
          [700, 700, 400, 400, 300, 300, 300, 100, 100, 100],
          [400, 700, 700, 400, 400, 300, 300, 300, 100, 100],
          [400, 400, 700, 700, 400, 400, 300, 300, 300, 100],
          [300, 400, 400, 700, 700, 400, 400, 300, 300, 100],
          [300, 300, 400, 400, 700, 700, 400, 400, 300, 300],
          [100, 300, 300, 400, 400, 700, 700, 400, 400, 300],
          [100, 300, 300, 300, 400, 400, 700, 700, 400, 400],
          [100, 100, 100, 300, 300, 400, 400, 700, 700, 400],
          [100, 100, 100, 300, 300, 300, 400, 400, 700, 700]
        ],
       state_index;

    function change_name(state_index){
      for(var i=1; i <= 10; i++) {
        var letter = $("#name_" + i);
        letter.attr("font-weight", states[state_index][i-1]);
      }
    }
       
    function update_state(mouse_x) {
      var $name =  $("#head"),
          state = 0,
          pos = ((mouse_x - $name.offset().left)/$name.width()) * 10;

        if(pos > 0 && pos < 10){
          console.log(pos);
        }
    

    }

    update_state($event.clientX);
  };

  $scope.upload = function() {
    console.log('upload');
  };

})

;

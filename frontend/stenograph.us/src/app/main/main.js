angular.module( 'transcribe-ninja.main', [
  'transcribe-ninja.feedback',
  'ui.router',
  'ngMask'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'main', {
    url: '/',
    views: {
      "main": {
        controller: 'MainCtrl',
        templateUrl: 'main/main.tpl.html'
      }
    },
    data:{ pageTitle: 'Стенографирование разговоров' }
  });
}])

.controller( 'MainCtrl', ["$scope", "$translate", "SmartPlurals", "$modal", function MainCtrl( $scope, $translate, SmartPlurals, $modal) {
  $translate.use("ru");
  var pluralRule = SmartPlurals.getRule('ru');

  $scope.calculator_hours = 1;


  $scope.select_calculator = function () {
    var $calculator = $("#calculator");

    yaCounter30919251.reachGoal('calculator');

    setTimeout(function () { $("#calculator").select(); }, 50); //select all text in any field on focus for easy re-entry. Delay sightly to allow focus to "stick" before selecting.

  }

  $scope.calculator = function (hours) {
    var price = 15;
    
    if(hours > 10) {
      price = 12;
    }

    return hours * price * 60
  }

  $scope.callback = function (record) {
    yaCounter30919251.reachGoal('callback-open');

    $modalInstance = $modal.open(
    {
      templateUrl: 'feedback/callback.modal.tpl.html',
      controller: 'FeedbackModalCtrl',
      windowClass: 'feedback-callback'
    });
  };
}])

;

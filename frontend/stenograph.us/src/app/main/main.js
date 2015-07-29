angular.module( 'transcribe-ninja.main', [
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

.controller( 'MainCtrl', ["$scope", "$translate", "SmartPlurals", function MainCtrl( $scope, $translate, SmartPlurals) {
  $translate.use("ru");
  var pluralRule = SmartPlurals.getRule('ru');

  $scope.calculator_hours = 1;

}])

;

angular.module( 'transcribe-ninja.about', [
  'ui.router',
  'ngMask'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'about', {
    url: '/about',
    views: {
      "main": {
        controller: 'AboutCtrl',
        templateUrl: 'about/about.tpl.html'
      }
    },
    data:{ pageTitle: 'Стенографирование разговоров' }
  });

  $stateProvider.state( 'contacts', {
    url: '/about/contacts',
    views: {
      "main": {
        controller: 'AboutCtrl',
        templateUrl: 'about/about.contacts.tpl.html'
      }
    },
    data:{ pageTitle: 'Стенографирование разговоров' }
  });
}])

.controller( 'AboutCtrl', ["$scope", "$translate", function AboutCtrl( $scope, $translate) {
  $translate.use("ru");


}])

;

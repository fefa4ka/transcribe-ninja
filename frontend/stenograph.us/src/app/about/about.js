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

.controller( 'AboutCtrl', ["$scope", "$translate", "$modal", function AboutCtrl( $scope, $translate, $modal) {
  $translate.use("ru");


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

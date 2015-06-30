angular.module( 'transcribe-ninja.history', [
  'transcribe-ninja.history.detail',
  'ui.router',
  'diff-match-patch'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'history', {
    url: '/history',
    views: {
      "main": {
        controller: 'HistoryCtrl',
        templateUrl: 'history/history.tpl.html'
      }
    },
    data: { 
      pageTitle: 'История вашей работы',
      requireLogin: true
    }
  });
}])

.controller( 'HistoryCtrl', ["$scope", "api", "$translate", "$modal", "$rootScope", function HistoryCtrl( $scope, api, $translate, $modal, $rootScope) {
  $translate.use("ru");
  
  function getDateBefore(days) {
    var date = new Date();
    date.setDate(date.getDate() - days);
    var year = date.getFullYear();
    var month = (1 + date.getMonth()).toString();
    month = month.length > 1 ? month : '0' + month;
    var day = date.getDate().toString();
    day = day.length > 1 ? day : '0' + day;
    
    return year + '-' + month + '-' + day;
  }

  $scope.uncheckedQueues = api.history.list({ unchecked: true });
  $scope.checkedQueues = api.history.list({ checked: true, min_mistakes: 1 });
  // $scope.checkedQueues = api.history.list({ checked: true });

  $scope.statistics = [api.statistics.get({ 'after_date': getDateBefore(1) }), api.statistics.get({ 'after_date': getDateBefore(7) }), api.statistics.get({ 'after_date': getDateBefore(31) }), api.statistics.get()];
  $scope.statisticsDescription = ['За день', 'За неделю', 'За месяц', 'За всё время'];
  
  $scope.uncheckedStatistics = api.statistics.get({ 'unchecked': true });

  $scope.uncheckedPageChanged = function() {
    api.history.list({ unchecked: true, page: $scope.uncheckedQueuePage }).
      $promise.then(function(data) {
        $scope.uncheckedQueues.results = data.results;
      });
  };

  $scope.chekedPageChanged = function() {
    api.history.list({ checked: true, page: $scope.uncheckedQueuePage }).
      $promise.then(function(data) {
        $scope.checkedQueues.results = data.results;
      });
  };


  $scope.queueDetail = function (queue) {
    $modalInstance = $modal.open(
    {
      templateUrl: 'history/detail/history.detail.tpl.html',
      controller: 'HistoryDetailModalCtrl',
      windowClass: 'history-detail',
      resolve: {
        queue: function () {
          return queue;
        }
      }
    });
  };
                  
  // Ya.Metrica
  yaCounter27735045.reachGoal('history');



}])

;
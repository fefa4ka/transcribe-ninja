angular.module( 'transcribe-ninja.history', [
  'transcribe-ninja.history.detail',
  'transcribe-ninja.history.payment',
  'ui.router',
  'tabs',
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

.controller( 'HistoryCtrl', ["$scope", "$rootScope", "api", "$translate", "$modal", function HistoryCtrl( $scope, $rootScope, api, $translate, $modal) {
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
  $scope.uncheckedQueuePage = 1;
  $scope.checkedQueuePage = 1;
  // $scope.checkedQueues = api.history.list({ checked: true });

  $scope.statistics = [
    api.statistics.get({ 'after_date': getDateBefore(1) }), 
    api.statistics.get({ 'after_date': getDateBefore(7) }), 
    api.statistics.get({ 'after_date': getDateBefore(31) }), 
    api.statistics.get()
  ];

  $scope.total_checked = $scope.statistics[$scope.statistics.length - 1];

  $scope.payments = api.payment.list();

  $scope.paymentsPageChanged = function() {
    api.payment.list({ page: $scope.paymentsPage }).
      $promise.then(function(data) {
        $scope.payments.results = data.results;
      });
  };

  $scope.statisticsDescription = [
    'За сегодня', 
    'За эту неделю', 
    'За последний месяц', 
    'За всё время'
  ];
  
  $scope.uncheckedStatistics = api.statistics.get({ 'unchecked': true });

  $scope.uncheckedPageChanged = function() {
    api.history.list({ unchecked: true, page: $scope.uncheckedQueuePage }).
      $promise.then(function(data) {
        $scope.uncheckedQueues.results = data.results;
      });
  };

  $scope.checkedPageChanged = function() {
    api.history.list({ checked: true, page: $scope.checkedQueuePage }).
      $promise.then(function(data) {
        $scope.checkedQueues.results = data.results;
      });
  };

 $scope.takeMoney = function (amount) {
    $modalInstance = $modal.open(
    {
      templateUrl: 'history/payment/history.payment.tpl.html',
      controller: 'PaymentModalCtrl',
      windowClass: 'payment-bill',
      resolve: {
        amount: function () {
          return amount;
        },
        callback: function () {
          return function () {
            api.account.get().
              $promise.
                then(function (data) {
                  $rootScope.currentUser = data;
                });

            $scope.payments = api.payment.list();
          };
        }
      }
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
  // yaCounter27735045.reachGoal('history');



}])

;

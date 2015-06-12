angular.module( 'transcribe-ninja.record.list', [
  'transcribe-ninja.order',
  'ui.router'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'record-list', {
    url: '/records',
    views: {
      "main": {
        controller: 'RecordListCtrl',
        templateUrl: 'record/list/list.tpl.html'
      }
    },
    data:{ 
      pageTitle: 'Ваши записи',
      requireLogin: true
     }
  });
}])

.controller( 'RecordListCtrl', ["$scope", "$translate", "$modal", "$log", "$interval", "api", function RecordCtrl( $scope, $translate, $modal, $log, $interval, api ) {
  $translate.use("ru");

  $interval(function () {
     api.record.list().
      $promise.
        then(function (data) {
          $scope.records = data;
        });
  }, 5000);

  $scope.records = api.record.list();

  $scope.upload = function() {
    $('input[type=file]').click();
  };

  $scope.remove = function ( record ) {
    record.trashed_at = Date.now();

    api.record.remove({ recordId: record.id });

    return record;
  };

  $scope.order = function (record) {
    $modalInstance = $modal.open(
    {
      templateUrl: 'order/order.modal.tpl.html',
      controller: 'OrderModalCtrl',
      windowClass: 'order-bill',
      resolve: {
        record: function () {
          return record;
        }
      }
    });
  };

}])

;

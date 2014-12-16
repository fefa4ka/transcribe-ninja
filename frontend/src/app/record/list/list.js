angular.module( 'transcribe-ninja.record.list', [
  'transcribe-ninja.order',
  'ui.router'
])

.config(function config( $stateProvider ) {
  $stateProvider.state( 'record-list', {
    url: '/records',
    views: {
      "main": {
        controller: 'RecordListCtrl',
        templateUrl: 'record/list/list.tpl.html'
      }
    },
    data:{ pageTitle: 'Ваши записи' }
  });
})

.controller( 'RecordListCtrl', function RecordCtrl( $scope, $translate, $modal, $log, api ) {
  $translate.use("ru");
  $scope.records = api.record.list();
  $log.log($scope.records);

  $scope.upload = function() {
    $('input[type=file]').click();
  }
  
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

})

;

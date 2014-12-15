angular.module( 'transcribe-ninja.record.list', [
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

  $scope.remove = function ( record ) {
    record.trashed_at = Date.now();

    api.records.remove({ recordId: record.id });

    return record;
  };

  $scope.order = function (record) {
    $modalInstance = $modal.open({
      templateUrl: 'record/list/list.order.tpl.html',
      controller: function($scope, $modalInstance, record){
        $scope.record = record;

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');
        };
        
    },
    resolve: {
        record: function () {
          return record;
        }
      },
      size: 'sm'
      });
  };

})

;

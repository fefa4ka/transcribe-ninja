angular.module( 'transcribe-ninja.order', [
  'ui.router'
])

.config(function config( $stateProvider ) {

})

.controller( 'OrderModalCtrl', function OrderModalCtrl( $scope, $modalInstance, record, api ) {
    $scope.record = record;

    $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
    };

    $scope.order = function (record) {
        api.order.create({
            record: record.id,
            start_at: 0,
            end_at: record.duration
        });
    };

})

;

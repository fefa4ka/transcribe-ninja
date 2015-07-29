angular.module( 'transcribe-ninja.order', [
  'ui.router',
  'ui.checkbox'
])

.config(["$stateProvider", function config( $stateProvider ) {

}])

.controller( 'OrderModalCtrl', ["$scope", "$modalInstance", "record", "callback", "api", function OrderModalCtrl( $scope, $modalInstance, record, callback, api ) {
    $scope.record = record;
    $scope.callback = callback;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.order = function (record) {
        api.order.create({
            record: record.id,
            start_at: 0,
            end_at: record.duration,
            editing: $scope.editing,
            speedup: $scope.speedup
        });

        // Если есть коллбэк
        if(angular.isUndefined($scope.callback) === false) {
            $scope.callback();
        }
        
        $modalInstance.dismiss('cancel');


    };

}])

;

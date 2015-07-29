angular.module( 'transcribe-ninja.order', [
  'ui.router',
  'ui.checkbox',
  'tabs'
])

.config(["$stateProvider", function config( $stateProvider ) {

}])

.controller( 'OrderModalCtrl', ["$scope", "$modalInstance", "record", "callback", "api", "$modal", function OrderModalCtrl( $scope, $modalInstance, record, callback, api, $modal ) {
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
        }, function () {
            // Если есть коллбэк
            if(angular.isUndefined($scope.callback) === false) {
                $scope.callback();
            }
        }, function () {
            var total = $scope.record.duration / 60 * (15 + $scope.editing * 5 + $scope.speedup * 5);
            $scope.payment(total);
        });

        
        
        $modalInstance.dismiss('cancel');


    };

    $scope.payment = function (amount) {
        $modalInstance = $modal.open(
        {
          templateUrl: 'payment/payment.modal.tpl.html',
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
              };
            }
          }
        });
        };


}])

;

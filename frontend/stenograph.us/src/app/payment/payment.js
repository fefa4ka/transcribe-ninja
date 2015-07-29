angular.module( 'transcribe-ninja.payment', [
  'ui.router',
  'ngMask',
  'tabs'
])

.config(["$stateProvider", function config( $stateProvider ) {

}])

.controller( 'PaymentModalCtrl', ["$scope", "$modalInstance", "amount", "callback", "api", function PaymentModalCtrl( $scope, $modalInstance, amount, callback, api ) {
    $scope.amount = amount; 
    $scope.callback = callback;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.takeMoney = function (payment_type) {
        var destination = "";

        switch (payment_type) {
            case 1:
                comment = "Оплата по счёту";
                destination = $scope.card;
                break;
            case 2:
                comment = "Оплата на QIWI Кошелёк";
                destination = $scope.qiwi;
                break;
            case 3:
                comment = "Снятие на Яндекс.Деньги";
                destination = $scope.yandex;
                break;
            case 4:
                comment = "Другой способ оплаты";
                destination = $scope.other;
                break;
        }

        yaCounter30919251.reachGoal('payment-send');

        api.payment.create({
            comment: comment,
            destination: destination
        }, function () {
            if(angular.isUndefined($scope.callback) === false) {
                $scope.callback();
            }
        });

        
        $modalInstance.dismiss('cancel');


    };

}])

;

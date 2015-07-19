angular.module( 'transcribe-ninja.history.payment', [
  'ui.router',
  'ngMask'
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
                comment = "Снятие денег на телефон";
                destination = $scope.phone;
                break;
            case 2:
                comment = "Снятие денег на карту";
                destination = $scope.card;
                break;
            case 3:
                comment = "Снятие денег на QIWI";
                destination = $scope.qiwi;
                break;
            case 4:
                comment = "Снятие на Яндекс.Деньги";
                destination = $scope.yandex;
                break;
        }

    
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

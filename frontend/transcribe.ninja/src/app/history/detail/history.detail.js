angular.module( 'transcribe-ninja.history.detail', [
  'ui.router'
])

.config(["$stateProvider", function config( $stateProvider ) {

}])

.controller( 'HistoryDetailModalCtrl', ["$scope", "$modalInstance", "queue", "api", function HistoryDetailModalCtrl( $scope, $modalInstance, queue, api ) {
    $scope.queue = queue;
    $scope.diff = api.queue.get({ queueId: queue.id });
   
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.review = function (queue) {



        $modalInstance.dismiss();
    };

}])

;

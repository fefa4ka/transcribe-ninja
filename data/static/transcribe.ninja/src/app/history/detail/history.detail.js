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

    // Ya.Metrica
    if($scope.queue.checked) {
        yaCounter27735045.reachGoal('checked_mistakes_view');
    } else {
        yaCounter27735045.reachGoal('unchecked_mistakes_view');
    }

}])

;

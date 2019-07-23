angular.module('ob.time', ['ob.core'])
.directive('obTime', function (obRestApi) {
  return {
    restrict: 'E',
    scope: {
      "obName": "=",
      "obValue": "="
    },
    templateUrl: 'html/ob-time.html',
    controller: function ($scope) {
      var stream = obRestApi.stream($scope.obName);
      stream.sub.data(function () {
        $scope.obDate = new Date($scope.obValue.$date);
      });
      stream.open();
    }
  };
});
angular.module('ob.time', ['ob.core'])
.directive('obTime', function (obRestApi) {
  return {
    restrict: 'E',
    scope: {
      "name": "=",
      "item": "="
    },
    templateUrl: 'html/ob-time.html',
    controller: function ($scope) {
      var stream = obRestApi.stream($scope.name);
      stream.sub.data(function () {
        $scope.date = new Date($scope.item.value.$date);
      });
      stream.open();
    }
  };
});
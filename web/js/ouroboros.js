angular.module('ouroboros', ['ob.core', 'ob.time', 'ob.math'])
.directive('ouroboros', function (obRestApi) {
  return {
    restrict: 'E',
    scope: {
      "name": "@"
    },
    templateUrl: 'html/ouroboros.html',
    controller: function ($scope) {
      $scope.groups = {};
      
      var stream = obRestApi.stream($scope.name);
      stream.sub.data(function () {
        stream.data.forEach(function (d) {
          $scope.groups[d.key.$tuple[0]] = $scope.groups[d.key.$tuple[0]] || {};
          $scope.groups[d.key.$tuple[0]][d.key.$tuple[1]] = d.value;
        });
      });
      stream.open();
      
      $scope.isNumber = function (value) {
        return angular.isNumber(value);
      };
    }
  };
});
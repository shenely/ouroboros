angular.module('ouroboros', ['ob.core', 'ob.time', 'ob.math'])
.directive('ouroboros', function (obRestApi) {
  return {
    restrict: 'E',
    scope: {
      "name": "@"
    },
    templateUrl: 'html/ouroboros.html',
    controller: function ($scope) {
      var stream = obRestApi.stream($scope.name);
      $scope.data = stream.data;
      $scope.ctrl = stream.ctrl;
      stream.open();
      
      $scope.isNumber = function (value) {
        return angular.isNumber(value);
      };
    }
  };
});
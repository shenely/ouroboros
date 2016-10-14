angular.module('ob.math', [])
.directive('obArray', function () {
  return {
    restrict: 'E',
    scope: {
      "obValue": "="
    },
    templateUrl: 'html/ob-array.html',
    controller: function ($scope) { }
  };
});
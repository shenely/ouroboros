angular.module('ob.math', ['ob.core'])
.directive('obArray', function (obRestApi) {
  return {
    restrict: 'E',
    scope: {
      "item": "="
    },
    templateUrl: 'html/ob-array.html',
    controller: function ($scope) { }
  };
});
angular.module('ob.time', ['angular-websocket']);
.directive('obTime', function (obRestApi) {
  return {
    restrict: 'E',
    scope: {
      "name": "@",
      "field": "@?",
    },
    templateUrl: 'html/ob-time.html',
    controller: function ($scope) {
      var ws = obRestApi.system.ws($scope.name);
      ws.sub.data(function () {
        var item = ws.data.find(function (d, i) {
          return angular.equals(d.key.$tuple, [$scope.field || true, "t_dt"]);
        });
        $scope.date = new Date(item ? item.value.$date : 0);
      });
      ws.open();
    }
  };
});
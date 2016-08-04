var app = angular.module('obApp', ['angular-websocket']);

app.factory("obRestApi", function ($location, $http, $websocket) {
  var location = $location.host() + ":" + $location.port(),
      restApi =  location + "/ob-rest-api",
      systemRest = "http://" + restApi + "/system",
      processRest = "http://" + restApi + "/proess",
      socket = $websocket("ws://" + restApi + "/stream");
  
  var handlers = {},
      callers = {},
      data = {}, ctrl = {};
  
  socket.onMessage(function (event) {
    var obj = angular.fromJson(event.data);
    if (obj.name in handlers) {
      handlers[obj.name].forEach(function (handler) { handler(obj); });
    }
  });
  
  return {
    "all": function () { return $http.get("http://" + caduceus) },
    "system": {
      "get": function (name) { return $http.get(systemRest + "?name=" + name) },
      "post": function (config) { return $http.post(systemRest, {"data": config}) },
      "delete": function (config) { return $http.delete(systemRest + "?name=" + name) },
      "ws": function (name) {
        handlers[name] = handlers[name] || [];
        callers[name] = callers[name] || { "data": [], "ctrl": [] };
        data[name] = data[name] || [];
        ctrl[name] = ctrl[name] || [];
        
        var handler = function (obj) {              
          if (obj.data !== undefined) {
            obj.data.forEach(function (o) {
              d = data[name].find(function (d) {
                return angular.equals(d.key.$tuple, o.key.$tuple);
              });
              (d !== undefined) ? (d.value = o.value)
                                : data[name].push(o);
            });
            callers[name].data.forEach(function (callback) { callback(); });
          }

          if (obj.ctrl !== undefined) {
            obj.ctrl.forEach(function (o) {
              d = ctrl[name].find(function (d) {
                return angular.equals(d.key, o);
              });
              (d !== undefined) ? (d.value = true)
                                : ctrl[name].push({ "key": o, "value": true });
            });
            callers[name].ctrl.forEach(function (callback) { callback(); });
            ctrl[name].forEach(function (d) { d.value = false; });
          }
        };
        
        return {
          "data": data[name], "ctrl": ctrl[name],
          "pub": {
            "data": function (values) { socket.send(angular.toJson({"data": values})) },
            "ctrl": function (keys) { socket.send(angular.toJson({"ctrl": keys})) }
          },
          "sub": {
            "data": function (callback) { callers[name].data.push(callback); },
            "ctrl": function (callback) { callers[name].ctrl.push(callback); }
          },
          "open": function () { handlers[name].push(handler); },
          "close": function () {
            var index = handlers[name].indexOf(function (d) {
              return d.fn === handler;
            });
            handlers[name].splice(index, 1);
          }
        };
      }
    }
  };
})
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
var app = angular.module('caduceus', ['angular-websocket']);

app.factory("model", function ($location, $http, $websocket) {
  var location = $location.host() + ":" + $location.port(),
      caduceus =  location + "/caduceus.py",
      socket = $websocket("ws://" + location + "/caduceus-stream");
  
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
      "get": function (name) { return $http.get("http://" + caduceus + "?name=" + name) },
      "post": function (config) { return $http.post("http://" + caduceus, {"config":config}) },
      "delete": function (config) { return $http.delete("http://" + caduceus + "/" + name) },
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
.directive('caduceusTime', function (model) {
  return {
    restrict: 'E',
    scope: {
      "name": "@",
      "field": "@?",
    },
    templateUrl: 'html/caduceus-time.html',
    controller: function ($scope) {
      var ws = model.system.ws($scope.name);
      ws.sub.data(function () {
        var item = ws.data.find(function (d, i) {
          return angular.equals(d.key.$tuple, [$scope.field || true, "t_dt"]);
        });
        $scope.date = new Date(item ? item.value.$date : 0);
      });
      ws.open();
    }
  };
})
.directive('caduceus', function() {
  return {
    restrict: 'E',
    scope: {},
    templateUrl: 'html/caduceus.html',
    controller: function ($scope, model) {
      var ws;
      
      $scope.index = {"system":0, "process":0};
      $scope.all = {"system":[], "process":[]};
      
      model.all().then(function (response) {
        $scope.all.system = response.data.result.system;
        $scope.all.process = response.data.result.process;
      });

      $scope.onChange = function () {
        if (ws !== undefined) { ws.close(); }
        
        model.system.get($scope.all.system[$scope.index.system])
        .then(function (response) {
          $scope.system = response.data.result;
          
          ws = model.system.ws($scope.system.name);
          $scope.data = ws.data;
          ws.open();
        });
      };
    }
  };
});
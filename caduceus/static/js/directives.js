angular.module('kepler.directives', [])
	.directive('universe', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: UniverseControl
		};
	})
	.directive('planet', function() {
		return {
			restrict: 'E',
			scope: true,
			priority: 1,
			controller: PlanetControl
		};
	})
	.directive('earth', function() {
		return {
			restrict: 'A',
			scope: true,
			priority: 10,
			controller: EarthControl
		};
	})
	.directive('ground', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: GroundControl
		};
	})
    .directive('background', function() {
        return {
            restrict: 'A',
            scope: true,
            controller: BackgroundControl
        };
    })
    .directive('foreground', function() {
        return {
            restrict: 'A',
            scope: true,
            controller: ForegroundControl
        };
    })
	.directive('sea', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: SeaControl
		};
	})
	.directive('land', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: LandControl
		};
	})
	.directive('countries', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: CountriesControl
		};
	})
	.directive('graticule', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: GraticuleControl
		};
	})
	.directive('footPrint', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: FootPrintControl
		};
	})
	.directive('groundTrack', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: GroundTrackControl
		};
	})
	.directive('space', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: SpaceControl
		};
	})
	.directive('trailPath', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: TrailPathControl
		};
	})
	.directive('spaceCraft', function() {
		return {
			restrict: 'A',
			scope: true,
			controller: SpaceCraftControl
		};
	});

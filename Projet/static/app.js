var app = angular.module('web', []);

app.controller('Accueil', function($scope, $http){
	$http.post('http://localhost:5000/', "").success(function(data, status) {
		$scope.bienvenue = data[0];
		data.shift();
		$scope.rubriques = data;		
	}).error(function(data){
	});
});

app.controller('Concert', function($scope, $http){

	$http.post('http://localhost:5000/Concert', {'type': "all"}).success(function(data){
		$scope.concerts = data;

		dates_dup = [];
		cat_dup = [];
		for(i in data){
			dates_dup.push(data[i].date.substring(0,7)+"-01");
			cat_dup.push(data[i].style);
		}
		$scope.dates = suppDoubles(dates_dup);
		$scope.styles = suppDoubles(cat_dup);

	}).error(function(data){

	});

	$scope.filtre = 'all';
	$scope.modifFiltre = function(filt){
		$scope.filtre = filt;
	};

	suppDoubles = function(tab){
		res = [];
		for(i in tab){
			if(tab.indexOf(tab[i]) == i){
				res.push(tab[i]);
			}
		}
		return(res);
	}

});

app.controller('Connexion', function($scope, $http, $window){
	$scope.valid = true;
	$scope.user = {'username': '', 'password': ''};

	$scope.submit = function(){
		if($scope.user.username === '' || $scope.user.password === ''){
			$scope.valid = false;
			return;
		}
		else {
			$http.post('http://localhost:5000/Authenticate', $scope.user)
				.success(function(data){
					$scope.valid = true;
					$window.sessionStorage.token = data.token;
				})
				.error(function(data){
					$scope.valid = false;
					delete $window.sessionStorage.token;
				})
		}
		
	}

});

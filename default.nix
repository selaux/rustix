with import <nixpkgs> {};
python3Packages.buildPythonPackage rec {
  name = "${pname}-${version}";
  pname = "rustix";
  version = "0.1.0";
  src = ./.;
  buildInputs = [ python3 ];
  propagatedBuildInputs = [ python3Packages.pytoml ];
}

with import <nixpkgs> {};
python3Packages.buildPythonPackage rec {
  name = "${pname}-${version}";
  pname = "rustix";
  version = "0.1.0";
  src = lib.sourceByRegex ./. [ "^rustix.py$" "^setup.py$" ];
  buildInputs = [ python3 ];
  propagatedBuildInputs = [ python3Packages.pytoml ];
}

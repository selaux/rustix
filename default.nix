with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "rustix";
  version = "0.1.0";
  src = ./.;
  buildInputs = [ python3 python3Packages.pytoml ];
}

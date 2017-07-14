with import <nixpkgs> {};
let
    rustixDerivation = import ../../rustixDerivation.nix;
in
rustixDerivation {
  name = "mixed-dependencies";
  version = "0.1.0";
  src = ./.;
}
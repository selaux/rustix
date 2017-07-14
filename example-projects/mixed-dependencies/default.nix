with import <nixpkgs> {};
let
    rustixDerivation = import ../../rustixDerivation.nix;
in
rustixDerivation {
  name = "mixed-dependencies";
  version = "0.1.0";
  src = lib.sourceByRegex ./. [ "^src.*$" "^Cargo.toml$" "^Cargo.lock$" ];

  additionalChecksums = [
    {
        identifer="getopts 0.2.14 (git+https://github.com/rust-lang-nursery/getopts.git)";
        sha256="0q0jpz4pv28vz4qv79x62qbgdpwxpwb4zfkdd16djnkj8r7qn6yp";
    }
  ];
}
let
    host_pkgs = import <nixpkgs> {};
    nixpkgs = host_pkgs.fetchFromGitHub {
        owner = "P-E-Meunier";
        repo = "nixpkgs";
        rev = "c642489a301f4b672fdf1701384f15c9148c709e";
        sha256 = "0q16mrifadb3q3b9r1ijaabqd9ry9x11ym0gc9jklrg66sbjjaw3";
    };
    rustix = import ./default.nix;
in
with import nixpkgs {};
cfg:
let
    additionalChecksums = builtins.foldl' (deps: dep: deps + "--additional-checksum '${dep.identifer}' '${dep.sha256}'") "" cfg.additionalChecksums;
    rustixDerivaton = stdenv.mkDerivation {
        name = "${cfg.name}-rustix";
        inherit (cfg) version src;

        buildPhase = ''
            ${rustix}/bin/rustix.py $src ${additionalChecksums} > ./Cargo.lock.nix
        '';

        installPhase = ''
            mkdir -p $out
            ln -s $src/* $out
            cp ./Cargo.lock.nix $out
        '';
    };
in
    import "${rustixDerivaton}/Cargo.lock.nix" { inherit mkRustCrate fetchurl fetchgit; } rustc
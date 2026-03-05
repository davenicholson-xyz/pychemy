{
  description = "Pychemy - Wallhaven Gallery desktop app";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: [ ps.pywebview ]);
        pychemy = pkgs.stdenv.mkDerivation {
          pname = "pychemy";
          version = "0.1.0";
          src = ./.;
          nativeBuildInputs = [ pkgs.makeWrapper ];
          dontBuild = true;
          installPhase = ''
            mkdir -p $out/share/pychemy $out/bin
            cp main.py ui.html $out/share/pychemy/
            makeWrapper ${pythonEnv}/bin/python $out/bin/pychemy \
              --add-flags "$out/share/pychemy/main.py" \
              --set QTWEBENGINE_DISABLE_SANDBOX 1
          '';
        };
      in {
        packages.default = pychemy;
        apps.default = { type = "app"; program = "${pychemy}/bin/pychemy"; };
        devShells.default = pkgs.mkShell {
          packages = [ pythonEnv ];
          shellHook = ''
            echo "Pychemy dev shell ready — run: python main.py"
            export QTWEBENGINE_DISABLE_SANDBOX=1
          '';
        };
      });
}

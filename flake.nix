{
  description = "Pyvista - Wallhaven Gallery desktop app";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: [ ps.pywebview ]);
        pyvista = pkgs.stdenv.mkDerivation {
          pname = "pyvista";
          version = "0.1.0";
          src = ./.;
          nativeBuildInputs = [ pkgs.makeWrapper ];
          dontBuild = true;
          installPhase = ''
            mkdir -p $out/share/pyvista $out/bin
            cp main.py ui.html $out/share/pyvista/
            makeWrapper ${pythonEnv}/bin/python $out/bin/pyvista \
              --add-flags "$out/share/pyvista/main.py" \
              --set QTWEBENGINE_DISABLE_SANDBOX 1
          '';
        };
      in {
        packages.default = pyvista;
        apps.default = { type = "app"; program = "${pyvista}/bin/pyvista"; };
        devShells.default = pkgs.mkShell {
          packages = [ pythonEnv ];
          shellHook = ''
            echo "Pyvista dev shell ready — run: python main.py"
            export QTWEBENGINE_DISABLE_SANDBOX=1
          '';
        };
      });
}

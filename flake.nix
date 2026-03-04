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
      in {
        devShells.default = pkgs.mkShell {
          packages = [ pythonEnv ];
          shellHook = ''
            echo "Pychemy dev shell ready — run: python main.py"
            export QTWEBENGINE_DISABLE_SANDBOX=1
          '';
        };
      });
}

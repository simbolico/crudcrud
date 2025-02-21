{ pkgs }: {
  deps = [
    pkgs.python312Full
    pkgs.poetry
    pkgs.iproute2
    pkgs.libxcrypt
    pkgs.python312Packages.pytest
  ];
  env = {
    POETRY_HOME = "$HOME/.config/poetry";
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libxcrypt
    ];
    ID_NO_DETECT_GCP_AMBIENT = "1"; # Disable GCP ambient credential detection
  };
}
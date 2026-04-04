"use strict";
const fs = require("fs");
const path = require("path");
const cwd = process.env.INIT_CWD || process.cwd();
fs.writeFileSync(path.join(cwd, "postinstall-ran.txt"), "ok\n");

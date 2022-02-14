import * as fs from "fs";
import * as path from "path";

export const getAllFiles = (
  dirPath: string,
  arrayOfFiles: string[]
): string[] => {
  const files = fs.readdirSync(dirPath);
  arrayOfFiles = arrayOfFiles || ([] as string[]);

  files.forEach((file) => {
    if (fs.statSync(dirPath + "/" + file).isDirectory()) {
      arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
    } else {
      arrayOfFiles.push(path.join(__dirname, dirPath, "/", file));
    }
  });

  return arrayOfFiles;
};

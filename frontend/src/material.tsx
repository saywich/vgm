import React from "react";
import { createComponent } from "@lit/react";
import { MdFilledButton } from "@material/web/button/filled-button.js";
import { MdOutlinedButton } from "@material/web/button/outlined-button.js";
import { MdIconButton } from "@material/web/iconbutton/icon-button.js";

export const Button = createComponent({
  tagName: "md-filled-button",
  elementClass: MdFilledButton,
  react: React,
});
export const OutlineButton = createComponent({
  tagName: "md-outlined-button",
  elementClass: MdOutlinedButton,
  react: React,
});
export const IconButton = createComponent({
  tagName: "md-icon-button",
  elementClass: MdIconButton,
  react: React,
});

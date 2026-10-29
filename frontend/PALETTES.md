# Color palettes

The palettes are independent CSS files in `src/themes/light.css` and `src/themes/dark.css`. All page, panel, input, dialog, avatar, selected-row, message, and video-card backgrounds use neutral gray tokens. Blue is reserved for actions, focus indicators, links, and selected icons. Filled action buttons may use the accent; content surfaces never do.

| Token | Light | Dark |
| --- | --- | --- |
| Page background | `#FAFAFA` | `#121212` |
| Surface | `#FFFFFF` | `#1C1C1C` |
| Subtle surface | `#F5F5F5` | `#181818` |
| Raised surface | `#EEEEEE` | `#262626` |
| Hover surface | `#E8E8E8` | `#303030` |
| Selected surface | `#E0E0E0` | `#383838` |
| Primary text | `#171717` | `#F5F5F5` |
| Secondary text | `#525252` | `#C4C4C4` |
| Muted text | `#606060` | `#A3A3A3` |
| Border | `#D4D4D4` | `#404040` |
| Control outline | `#767676` | `#858585` |
| Blue accent | `#1D4ED8` | `#8AB4FF` |
| Text on accent | `#FFFFFF` | `#102347` |
| Error text | `#B42318` | `#FFB4AB` |
| Warning text | `#855500` | `#E7C46A` |

The default mode follows the OS. The System / Light / Dark selector is available before and after sign-in. An explicit choice persists across reloads and synchronizes across tabs. Browser chrome follows the selected neutral page color; the installed app's launch background defaults to neutral light.

To change the accent, edit `--primary` and `--on-primary` in each palette. The surface palette is unaffected.

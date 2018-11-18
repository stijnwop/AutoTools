# AutoTools

Maya tooling for the content creators.

#### Only supports Maya 2017 and above!

## Supports:
- Quick util functions
- UDIM

## How to install:

1. Open Maya
2. Open the Shelf editor
3. Click on the desired shelf
4. Create a new item (plus icon in the right part)
5. Name it: AutoTools
6. Click on the 'Command' tab
7. Check the checkbox that says "Python"

8. Copypaste the code below with the currect location to the AutoTools folder:
```python
import sys
sys.path.append('C:/Users/X/Documents/maya/201X/scripts/AutoTools')
import AutoTools
reload(AutoTools)
```
9. Go back to the 'Shelves' tab and click on the button 'Save All Shelves'

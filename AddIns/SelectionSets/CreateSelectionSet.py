import adsk.core
import adsk.fusion
import traceback

# Global set of event handlers to keep them referenced for the duration of the command
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Get the existing command definition or create it if it doesn't exist
        cmdDef = ui.commandDefinitions.itemById('FindBodiesCreateSelectionSet')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(
                'FindBodiesCreateSelectionSet',
                'Find Bodies and Create Selection Set',
                'Search for bodies by name and create a selection set',
                '')
        
        # Connect to the command created event
        onCommandCreated = FindBodiesCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # Execute the command
        cmdDef.execute()
        
        # Prevent this module from being terminated when the script returns
        adsk.autoTerminate(False)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Delete the command definition
        cmdDef = ui.commandDefinitions.itemById('FindBodiesCreateSelectionSet')
        if cmdDef:
            cmdDef.deleteMe()
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FindBodiesCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = FindBodiesCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FindBodiesCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)
            
            if not design:
                ui.messageBox('No active Fusion design found.')
                return
            
            # Get the body name to search for from user
            body_name, cancelled = ui.inputBox('Enter the exact body name to search for:', 
                                               'Find Bodies', '')
            
            if cancelled or not body_name.strip():
                return
            
            body_name = body_name.strip()
            
            # Find all matching bodies (as proxies in assembly context)
            matching_bodies = []
            root_comp = design.rootComponent
            
            # Check root component bodies
            for body in root_comp.bRepBodies:
                if body.name == body_name:
                    matching_bodies.append(body)
            
            # Check bodies in all occurrences
            all_occurrences = root_comp.allOccurrences
            for occ in all_occurrences:
                if occ.component:
                    for body in occ.component.bRepBodies:
                        if body.name == body_name:
                            # Create proxy for the body in the occurrence context
                            body_proxy = body.createForAssemblyContext(occ)
                            matching_bodies.append(body_proxy)
            
            # If no bodies found, show message and exit
            if len(matching_bodies) == 0:
                ui.messageBox(f'No bodies found with the name "{body_name}".')
                return
            
            # Create plural name for selection set
            plural_name = make_plural(body_name)
            
            # Get or create the selection set
            selection_sets = design.selectionSets
            selection_set = None
            action = "created"
            
            # Variables for tracking changes
            old_count = 0
            renamed_count = 0
            unchanged_count = 0
            added_count = 0
            
            # Check if selection set already exists
            for ss in selection_sets:
                if ss.name == plural_name:
                    selection_set = ss
                    action = "updated"
                    
                    # Analyze the old selection set before deleting
                    old_entities = selection_set.entities
                    old_count = len(old_entities)
                    
                    # Count how many items have been renamed (don't match the search name)
                    for i in range(len(old_entities)):
                        item = old_entities[i]
                        # Check if it's a BRepBody and if its name doesn't match
                        if hasattr(item, 'name') and item.name != body_name:
                            renamed_count += 1
                    
                    # Calculate unchanged count
                    unchanged_count = old_count - renamed_count
                    
                    break
            
            # Delete existing selection set if found
            if selection_set:
                selection_set.deleteMe()
            
            # Create new selection set with all matching bodies
            selection_set = selection_sets.add(matching_bodies, plural_name)
            
            # Calculate added count
            new_count = len(matching_bodies)
            added_count = new_count - unchanged_count
            
            # Show success message
            if action == "created":
                ui.messageBox(f'Found {new_count} {"body" if new_count == 1 else "bodies"} ' +
                             f'and created selection set: "{plural_name}"')
            else:
                message = f'Updated selection set: "{plural_name}"\n'
                message += f'Added {added_count}, Removed {renamed_count} (renamed), Unchanged {unchanged_count}\n'
                message += f'Total: {new_count} {"body" if new_count == 1 else "bodies"}'
                ui.messageBox(message)
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def make_plural(word):
    """
    Convert a singular word to its plural form using common English rules.
    """
    word_lower = word.lower()
    
    # Special cases dictionary
    special_cases = {
        'child': 'Children',
        'person': 'People',
        'man': 'Men',
        'woman': 'Women',
        'tooth': 'Teeth',
        'foot': 'Feet',
        'mouse': 'Mice',
        'goose': 'Geese',
        'ox': 'Oxen',
        'leaf': 'Leaves',
        'life': 'Lives',
        'knife': 'Knives',
        'wife': 'Wives',
        'half': 'Halves',
        'shelf': 'Shelves',
        'loaf': 'Loaves',
        'potato': 'Potatoes',
        'tomato': 'Tomatoes',
        'hero': 'Heroes',
        'echo': 'Echoes',
        'cactus': 'Cacti',
        'focus': 'Foci',
        'fungus': 'Fungi',
        'nucleus': 'Nuclei',
        'radius': 'Radii',
        'stimulus': 'Stimuli',
        'axis': 'Axes',
        'analysis': 'Analyses',
        'basis': 'Bases',
        'crisis': 'Crises',
        'diagnosis': 'Diagnoses',
        'thesis': 'Theses',
        'phenomenon': 'Phenomena',
        'criterion': 'Criteria',
        'datum': 'Data'
    }
    
    # Check special cases (case-insensitive)
    if word_lower in special_cases:
        # Preserve original capitalization pattern
        if word[0].isupper():
            return special_cases[word_lower]
        else:
            return special_cases[word_lower].lower()
    
    # Words ending in s, x, z, ch, sh -> add 'es'
    if word_lower.endswith(('s', 'x', 'z')) or word_lower.endswith(('ch', 'sh')):
        return word + 'es'
    
    # Words ending in consonant + y -> change y to ies
    if len(word) > 1 and word_lower.endswith('y') and word_lower[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    
    # Words ending in f or fe -> change to ves
    if word_lower.endswith('f'):
        return word[:-1] + 'ves'
    if word_lower.endswith('fe'):
        return word[:-2] + 'ves'
    
    # Words ending in consonant + o -> add 'es'
    if len(word) > 1 and word_lower.endswith('o') and word_lower[-2] not in 'aeiou':
        return word + 'es'
    
    # Default: just add 's'
    return word + 's'
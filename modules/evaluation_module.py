import os

from modules.gallery_module import Identity

def build_groundtruth(faces_path: str) -> dict[str, list[str]]:
    """
    Builds a dictionary of groundtruth faces.

    Args:
        faces_path: Path to the groundtruth faces.

    Returns:
        A dictionary of groundtruth faces.
    """
    groundtruth: dict[str, list[str]] = {}
    # Get all the names of the people in the groundtruth faces
    names = os.listdir(faces_path)
    for name in names:
        # Get all the frames where the person is present
        frames = os.listdir(os.path.join(faces_path, name))
        # Remove the extension from the frames
        frames = [frame.split(".")[0] for frame in frames]
        # For each frame, add the name to the groundtruth dictionary
        for frame in frames:
            if frame not in groundtruth:
                groundtruth[frame] = []
            groundtruth[frame].append(name)
    # Return the groundtruth dictionary
    return groundtruth

def list_to_dict_identities(identities: list[Identity]) -> dict[str, list[str]]:
    """
    Converts a list of identities to a dictionary of identities.
    
    Args:
        identities: List of identities.

    Returns:
        Dictionary of frame number and identity.
    """
    # Initialize the dictionary
    identities_dict: dict[str, list[str]] = {}
    # For each identity, add the frame number and the identity to the dictionary
    for identity in identities:
        # For each frame, add the identity to the dictionary
        for frame in identity.frames:
            identities_dict[frame] = identities_dict.get(frame, []) + [identity.name]
    # Return the dictionary
    return identities_dict

def evaluate_system(known_identities: list[Identity], groundtruth_faces_path: str):
    """
    Evaluates the system.

    Args:
        detected: List of detected identities.
        groundtruth_faces_path: Path to the groundtruth faces.
    """
    # Get the groundtruth faces
    groundtruth = build_groundtruth(groundtruth_faces_path)
    # Create detected dict
    detected = list_to_dict_identities(known_identities)
    # Get the frames where the system detected faces
    detected_frames = detected.keys()
    # Get the frames where the system didn't detect faces
    not_detected_frames = set(groundtruth.keys()) - set(detected_frames)
    extra_detected_frames = set(detected_frames) - set(groundtruth.keys())
    # Get the frames where the system detected faces but didn't detect the correct person
    incorrect_frames = set()
    false_positives: dict[str, list[str]] = {}
    false_negatives: dict[str, list[str]] = {}
    for frame in detected_frames:
        if groundtruth.get(frame) is None:
            # TODO: false positive?
            continue
        intesection = set(detected[frame]).intersection(set(groundtruth[frame]))
        # If the intersection is same length as the groundtruth, then the system detected the correct person
        if len(intesection) != len(groundtruth[frame]):
            incorrect_frames.add(frame)
            # Calculate the false positives. The false positives are the faces that the system detected but are not in the groundtruth
            false_positives[frame] = list(set(detected[frame]) - set(groundtruth[frame]))
            # Calculate the false negatives. The false negatives are the faces that are in the groundtruth but the system didn't detect
            false_negatives[frame] = list(set(groundtruth[frame]) - set(detected[frame]))
    # Get the frames where the system detected faces and detected the correct person
    correct_frames = set(detected_frames) - incorrect_frames
    # Calculate the precision
    precision = len(correct_frames) / len(detected_frames)
    # Calculate the recall
    
    recall = len(correct_frames) / len(groundtruth.keys())
    # Calculate the F1 score
    f1_score = 2 * precision * recall / (precision + recall)
    # Print the results
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1 score: ", f1_score)
    print("False positives: ", len(false_positives))
    print("False negatives: ", len(false_negatives))
    print("Not detected frames: ", len(not_detected_frames))

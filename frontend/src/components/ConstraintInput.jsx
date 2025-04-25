import { useState } from "react";
import { X, Plus } from "lucide-react";

export default function ConstraintInput({ logicalGroups, setLogicalGroups, mode }) {
  const [newLogicalOperator, setNewLogicalOperator] = useState("AND");
  const [newConstraints, setNewConstraints] = useState({});

  // Check if a structure constraint already exists
  const hasStructureConstraint = logicalGroups.some(group =>
    group.constraints.some(c => c.type === "structure")
  );

  // Base constraint types
  const baseConstraintTypes = [
    { value: "structure", label: "Structure (Points)" },
    { value: "word_inclusion", label: "Word Inclusion" },
    { value: "word_exclusion", label: "Word Exclusion" },
    { value: "object_inclusion", label: "Object Inclusion" },
    { value: "color_inclusion", label: "Color Inclusion" },
  ];

  // Filter constraint types based on mode
  const modeFilteredTypes = baseConstraintTypes.filter((type) => {
    if (mode === "text1" || mode === "text2") {
      return ["structure", "word_inclusion", "word_exclusion"].includes(type.value);
    } else if (mode === "image") {
      return ["object_inclusion", "color_inclusion"].includes(type.value);
    }
    return true;
  });

  const addLogicalGroup = () => {
    setLogicalGroups([...logicalGroups, { operator: newLogicalOperator, constraints: [] }]);
  };

  const addConstraint = (groupIndex) => {
    const newConstraint = newConstraints[groupIndex];
    if (!newConstraint?.type || !newConstraint?.value) return;

    // Prevent adding a structure constraint if one already exists
    if (newConstraint.type === "structure" && hasStructureConstraint) {
      alert("Only one structure constraint is allowed.");
      return;
    }

    // Prevent adding a structure constraint to a non-AND group
    if (newConstraint.type === "structure" && logicalGroups[groupIndex].operator !== "AND") {
      alert("Structure constraints can only be added to AND groups.");
      return;
    }

    const updatedGroups = [...logicalGroups];
    updatedGroups[groupIndex].constraints.push(newConstraint);
    setLogicalGroups(updatedGroups);

    // Clear the new constraint for this group
    setNewConstraints((prev) => ({
      ...prev,
      [groupIndex]: { type: "", value: "" },
    }));
  };

  const removeConstraint = (groupIndex, constraintIndex) => {
    const updatedGroups = [...logicalGroups];
    updatedGroups[groupIndex].constraints.splice(constraintIndex, 1);
    setLogicalGroups(updatedGroups);
  };

  const removeLogicalGroup = (groupIndex) => {
    const updatedGroups = [...logicalGroups];
    updatedGroups.splice(groupIndex, 1);
    setLogicalGroups(updatedGroups);

    setNewConstraints((prev) => {
      const updatedConstraints = { ...prev };
      delete updatedConstraints[groupIndex];
      return updatedConstraints;
    });
  };

  const handleNewConstraintChange = (groupIndex, field, value) => {
    setNewConstraints((prev) => ({
      ...prev,
      [groupIndex]: {
        ...prev[groupIndex],
        [field]: value,
      },
    }));
  };

  // Filter constraint types based on operator
  const getConstraintTypesForGroup = (operator) => {
    if (operator === "AND") {
      return modeFilteredTypes; // Allow all types for AND
    }
    // For OR and NOT, exclude "structure"
    return modeFilteredTypes.filter(type => type.value !== "structure");
  };

  return (
    <div>
      {/* Add Logical Group */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <select
          value={newLogicalOperator}
          onChange={(e) => setNewLogicalOperator(e.target.value)}
          style={{ padding: "0.5rem", border: "1px solid #e2e8f0", borderRadius: "0.25rem", flex: 1, backgroundColor: "#f9fafb" }}
        >
          <option value="AND">AND</option>
          <option value="OR">OR</option>
          <option value="NOT">NOT</option>
        </select>
        <button 
          onClick={addLogicalGroup} 
          style={{ 
            padding: "0.5rem", 
            backgroundColor: "#4a90e2", 
            color: "#ffffff", 
            borderRadius: "0.25rem",
            transition: "background-color 0.2s",
            border: "none",
            cursor: "pointer"
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = "#357abd"}
          onMouseOut={(e) => e.target.style.backgroundColor = "#4a90e2"}
        >
          <Plus size={20} />
        </button>
      </div>

      {/* Display Logical Groups */}
      {logicalGroups.map((group, groupIndex) => (
        <div key={groupIndex} style={{ marginBottom: "1rem", border: "1px solid #e2e8f0", borderRadius: "0.25rem", padding: "1rem", backgroundColor: "#f9fafb" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <span style={{ fontWeight: "500", color: "#1a1a1a" }}>Logical Operator: {group.operator}</span>
            <button 
              onClick={() => removeLogicalGroup(groupIndex)} 
              style={{ 
                backgroundColor: "transparent", 
                border: "none", 
                cursor: "pointer",
                color: "#ef4444"
              }}
            >
              <X size={20} />
            </button>
          </div>

          {/* Add Constraint */}
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
            <select
              value={newConstraints[groupIndex]?.type || ""}
              onChange={(e) => handleNewConstraintChange(groupIndex, "type", e.target.value)}
              style={{ padding: "0.5rem", border: "1px solid #e2e8f0", borderRadius: "0.25rem", flex: 1, backgroundColor: "#f9fafb" }}
            >
              <option value="">Select Constraint</option>
              {getConstraintTypesForGroup(group.operator).map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>

            <input
              type="text"
              placeholder="Enter value..."
              value={newConstraints[groupIndex]?.value || ""}
              onChange={(e) => handleNewConstraintChange(groupIndex, "value", e.target.value)}
              style={{ padding: "0.5rem", border: "1px solid #e2e8f0", borderRadius: "0.25rem", flex: 1, backgroundColor: "#f9fafb" }}
            />

            <button 
              onClick={() => addConstraint(groupIndex)} 
              style={{ 
                padding: "0.5rem", 
                backgroundColor: "#4a90e2", 
                color: "#ffffff", 
                borderRadius: "0.25rem",
                transition: "background-color 0.2s",
                border: "none",
                cursor: "pointer"
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = "#357abd"}
              onMouseOut={(e) => e.target.style.backgroundColor = "#4a90e2"}
            >
              Add
            </button>
          </div>

          {/* Display Constraints */}
          <ul>
            {group.constraints.map((c, constraintIndex) => (
              <li 
                key={constraintIndex} 
                style={{ 
                  display: "flex", 
                  justifyContent: "space-between", 
                  alignItems: "center", 
                  backgroundColor: "#f3f4f6", 
                  padding: "0.75rem", 
                  borderRadius: "0.25rem", 
                  marginBottom: "0.5rem",
                  color: "#1a1a1a"
                }}
              >
                <span>{c.type}: {c.value}</span>
                <button 
                  onClick={() => removeConstraint(groupIndex, constraintIndex)} 
                  style={{ 
                    backgroundColor: "transparent", 
                    border: "none", 
                    cursor: "pointer",
                    color: "#ef4444"
                  }}
                >
                  <X size={20} />
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
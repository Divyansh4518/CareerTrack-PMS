import math

class BPlusTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = [] # Holds Node objects if internal, Values if leaf
        self.next = None   # Pointer for leaf node linkage (crucial for range queries)

class BPlusTree:
    def __init__(self, order=4):
        self.root = BPlusTreeNode(is_leaf=True)
        self.order = order

    def search(self, key):
        """Search for a key in the B+ tree. Return the associated value if found, else None."""
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        
        for i, k in enumerate(node.keys):
            if k == key:
                return node.children[i]
        return None

    def insert(self, key, value):
        """Insert key-value pair into the B+ tree."""
        root = self.root
        if len(root.keys) == self.order - 1:
            # Root is full, tree grows in height
            temp = BPlusTreeNode()
            self.root = temp
            temp.children.append(root)
            self._split_child(temp, 0)
            self._insert_non_full(temp, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _insert_non_full(self, node, key, value):
        """Recursive helper to insert into a non-full node."""
        if node.is_leaf:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node.keys.insert(i, key)
            node.children.insert(i, value)
        else:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            if len(node.children[i].keys) == self.order - 1:
                self._split_child(node, i)
                # Route exactly equal keys to the right child
                if key >= node.keys[i]: 
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent, index):
        """Split the child at the given index."""
        node = parent.children[index]
        new_node = BPlusTreeNode(is_leaf=node.is_leaf)
        
        # Properly find the median based on the actual keys
        mid = len(node.keys) // 2  
        split_key = node.keys[mid]
        
        # Insert the median key into the parent
        parent.keys.insert(index, split_key)
        # Link the new node to the parent
        parent.children.insert(index + 1, new_node)
        
        if node.is_leaf:
            # For leaves: preserve the linked list structure and copy the middle key to the parent.
            new_node.keys = node.keys[mid:]
            new_node.children = node.children[mid:]
            
            node.keys = node.keys[:mid]
            node.children = node.children[:mid]
            
            # Maintain the linked list for range queries
            new_node.next = node.next
            node.next = new_node
        else:
            # For internal nodes: promote the middle key and split the children
            new_node.keys = node.keys[mid+1:]
            new_node.children = node.children[mid+1:]
            
            node.keys = node.keys[:mid]
            node.children = node.children[:mid+1]

    def range_query(self, start_key, end_key):
        """Return all key-value pairs where start_key <= key <= end_key."""
        result = []
        node = self.root
        
        # Find the starting leaf
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and start_key >= node.keys[i]:
                i += 1
            node = node.children[i]
            
        # Traverse the linked list of leaves
        while node is not None:
            for i, k in enumerate(node.keys):
                if start_key <= k <= end_key:
                    result.append((k, node.children[i]))
                elif k > end_key:
                    return result # Stop early since it's sorted
            node = node.next
        return result

    def delete(self, key):
        """Delete key from the B+ tree. Returns True if successful, False otherwise."""
        if not self.search(key):
            return False # Key doesn't exist
            
        self._delete(self.root, key)
        
        # If the root becomes empty but has a child, make the child the new root
        if len(self.root.keys) == 0 and not self.root.is_leaf:
            self.root = self.root.children[0]
            
        return True

    def _delete(self, node, key):
        """Recursive helper for deletion."""
        if node.is_leaf:
            # Base case: We are at the leaf, simply remove the key and its value
            for i, k in enumerate(node.keys):
                if k == key:
                    node.keys.pop(i)
                    node.children.pop(i)
                    return
        else:
            # Internal node: figure out which child to go to
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
                
            child = node.children[i]
            self._delete(child, key)
            
            # Post-deletion: Check for underflow (node has fewer keys than allowed)
            min_keys = math.ceil(self.order / 2) - 1
            if len(child.keys) < min_keys:
                self._handle_underflow(node, i)

    def _handle_underflow(self, parent, index):
        """Handle underflow by borrowing from siblings or merging."""
        child = parent.children[index]
        
        # Try borrowing from the left sibling
        if index > 0 and len(parent.children[index - 1].keys) > math.ceil(self.order / 2) - 1:
            left_sibling = parent.children[index - 1]
            if child.is_leaf:
                child.keys.insert(0, left_sibling.keys.pop())
                child.children.insert(0, left_sibling.children.pop())
                parent.keys[index - 1] = child.keys[0]
            else:
                child.keys.insert(0, parent.keys[index - 1])
                parent.keys[index - 1] = left_sibling.keys.pop()
                child.children.insert(0, left_sibling.children.pop())
            return

        # Try borrowing from the right sibling
        if index < len(parent.keys) and len(parent.children[index + 1].keys) > math.ceil(self.order / 2) - 1:
            right_sibling = parent.children[index + 1]
            if child.is_leaf:
                child.keys.append(right_sibling.keys.pop(0))
                child.children.append(right_sibling.children.pop(0))
                parent.keys[index] = right_sibling.keys[0]
            else:
                child.keys.append(parent.keys[index])
                parent.keys[index] = right_sibling.keys.pop(0)
                child.children.append(right_sibling.children.pop(0))
            return

        # If borrowing fails, we must merge
        if index > 0:
            self._merge(parent, index - 1) # Merge with left
        else:
            self._merge(parent, index)     # Merge with right

    def _merge(self, parent, index):
        """Merge child at index with its right sibling."""
        left_node = parent.children[index]
        right_node = parent.children[index + 1]
        
        if left_node.is_leaf:
            left_node.keys.extend(right_node.keys)
            left_node.children.extend(right_node.children)
            left_node.next = right_node.next # Maintain linked list!
        else:
            left_node.keys.append(parent.keys[index])
            left_node.keys.extend(right_node.keys)
            left_node.children.extend(right_node.children)
            
        parent.keys.pop(index)
        parent.children.pop(index + 1)
    
    def visualize_tree(self):
        """Generate Graphviz representation of the B+ tree structure."""
        from graphviz import Digraph
        dot = Digraph(comment='B+ Tree')
        dot.attr(rankdir='TB') 
        
        # FIX 1: Changed shape from 'record' to 'box' to avoid the Graphviz routing crash
        dot.attr('node', shape='box', style='filled', rounded='true', fontname='Helvetica')
        
        if len(self.root.keys) == 0:
            dot.node('empty', 'Empty Tree')
            return dot

        self._add_nodes(dot, self.root)
        self._add_edges(dot, self.root)
        
        # Draw the dashed red lines between leaf nodes
        curr = self.root
        while not curr.is_leaf:
            curr = curr.children[0]
            
        while curr and curr.next:
            node_id = str(id(curr))
            next_id = str(id(curr.next))
            dot.edge(node_id, next_id, style='dashed', color='red', constraint='false')
            curr = curr.next
            
        return dot

    def _add_nodes(self, dot, node):
        """Recursively add nodes to Graphviz object."""
        node_id = str(id(node))
        
        keys_str = " | ".join([str(k) for k in node.keys])
        fillcolor = 'lightgreen' if node.is_leaf else 'lightblue'
        
        # FIX 2: Removed the < > brackets from the label string
        dot.node(node_id, keys_str, fillcolor=fillcolor)
        
        if not node.is_leaf:
            for child in node.children:
                self._add_nodes(dot, child)

    def _add_edges(self, dot, node):
        """Add edges between nodes."""
        if not node.is_leaf:
            node_id = str(id(node))
            for child in node.children:
                child_id = str(id(child))
                dot.edge(node_id, child_id)
                self._add_edges(dot, child)
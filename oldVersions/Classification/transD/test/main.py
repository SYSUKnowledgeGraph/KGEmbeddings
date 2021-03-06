import numpy as np
import theano 
import theano.tensor as T
from dev_test import output_result

path = 'FB13_bern'

entity2id_fid = open('../'+path+'/entity2id.txt')
entity2id = {}
count = 0
for e in entity2id_fid :
    con = e.strip('\n').split(' ')
    entity2id[con[0]] = count
    count += 1
entity2id_fid.close()

relation2id_fid = open('../'+path+'/relation2id.txt')
relation2id = {}
count = 0
for e in relation2id_fid :
    con = e.strip('\n').split(' ')
    relation2id[con[0]] = count
    count += 1
relation2id_fid.close()



dev_fid = open('../'+path+'/dev.txt')
dev_data = dev_fid.readlines()
dev_fid.close()
dev_triples = []
n_dev = len(dev_data)
dev_triples_idx = np.zeros((n_dev, 3),'int32')
relation_list = set()
count = 0
for dev_t in dev_data:
    con = dev_t.strip('\n')
    dev_triples.append(con)
    h, r, t, label = con.split('\t')
    h_id = entity2id[h]
    r_id = relation2id[r]
    t_id = entity2id[t]
    dev_triples_idx[count] = np.asarray([h_id, r_id, t_id],'int32')
    count += 1
    relation_list.add(r)
print("hi watch this\n")    
print(len(dev_triples))

test_fid = open('../'+path+'/test.txt')
test_data = test_fid.readlines()
test_fid.close()
test_triples = []
n_test = len(test_data)
test_triples_idx = np.zeros((n_test, 3),'int32')
count = 0
for test_t in test_data:
    con = test_t.strip('\n')
    test_triples.append(con)
    h, r, t, label = con.split('\t') #\t
    h_id = entity2id[h]
    r_id = relation2id[r]
    t_id = entity2id[t]
    test_triples_idx[count] = np.asarray([h_id, r_id, t_id],'int32')
    count += 1
    relation_list.add(r)
relation_list = list(relation_list)
n_relation = len(relation_list)


print("hi watch this\n")    
print(len(test_triples))

print("hello\n")
print(n_relation)
print("hello\n")


def norm_matrix(matrix):
    return T.sum(T.sqr(matrix),axis=1)

def score():
    idx = T.imatrix('idx')
    ent_embed = T.matrix('ent_embed')
    rel_embed = T.matrix('rel_embed')
    #A_h_mat = T.tensor3('A_h_mat') #3D tensor means 
    #A_t_mat = T.tensor3('A_t_mat')
    Wr_embed = T.matrix('Wr_embed')
    We_embed = T.matrix('We_embed')
    h = ent_embed[idx[:,0]]
    r = rel_embed[idx[:,1]]
    t = ent_embed[idx[:,2]]
    #WE = W_embed[13:,:]
    #WR = W_embed[0:13,:]
    Wh = We_embed[idx[:,0]]
    Wr = Wr_embed[idx[:,1]]
    Wt = We_embed[idx[:,2]]
    #print("the h is ")
    #print(len(h),len(r),len(t))
    #print(h)

    #A_m = A_mat[idx[:,1]]
    #A_h = A_h_mat[idx[:,1]]
    #A_t = A_t_mat[idx[:,1]]

    #This function computes the dot product between the two tensors
    #
    #res = (t-np.dot(W,t)*W) - (h-(np.dot(h, W)*W)) - r  
    res =  t + np.dot(Wt,t)*Wr - (h + np.dot(Wh,h)*Wr) - r 
    #score = -norm_matrix(res)
    #score =-T.sum( T.abs_(res),axis=1)
    #res = h+r-t
    #res = res*res
    score = -T.sum( T.abs_(res),axis=1)
    #score = norm_matrix(res)
    return theano.function(inputs = [idx, ent_embed, rel_embed ,Wr_embed,We_embed],\
                           outputs = score,on_unused_input='ignore')
     #theano.function(inputs = [idx, ent_embed, rel_embed],\
                           #outputs = score,on_unused_input='ignore')
score_f = score()


    
entity2vec = np.loadtxt('../'+path+'/entity2vec.vec')
relation2vec = np.loadtxt('../'+path+'/relation2vec.vec')
Wr_embed = np.loadtxt('../'+path+'/Ar.vec')#.reshape((n_relation+6,100))
    #A_t = np.loadtxt('../TranSparse/A_t.bern'+str(i)).reshape((n_relation,20,20))
We_embed = np.loadtxt('../'+path+'/Ae.vec')
   
dev_score = score_f(dev_triples_idx, entity2vec,  relation2vec,Wr_embed,We_embed)
test_score = score_f(test_triples_idx, entity2vec, relation2vec,Wr_embed,We_embed)

output_result(dev_triples, dev_score, test_triples, test_score, relation_list)



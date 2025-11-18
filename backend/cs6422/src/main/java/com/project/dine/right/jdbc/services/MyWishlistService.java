package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IMyWishlistService;
import com.project.dine.right.jdbc.models.MyWishlist;
import com.project.dine.right.jdbc.repositories.MyWishlistRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class MyWishlistService implements IMyWishlistService {

    @Autowired
    private MyWishlistRepository myWishlistRepository;

    @Override
    public List<MyWishlist> findByUserId(Long userId) {
        return myWishlistRepository.findByUserId(userId);
    }

    @Override
    public Long countMyWishlists() {
        return myWishlistRepository.count();
    }
}
